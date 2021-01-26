import json

from pype.modules.ftrack.lib import BaseAction


def clone_review_session(session, entity):
    # Create a client review with timestamp.
    name = entity["name"]
    review_session = session.create(
        "ReviewSession",
        {
            "name": f"Clone of {name}",
            "project": entity["project"]
        }
    )

    # Add all invitees.
    for invitee in entity["review_session_invitees"]:
        session.create(
            "ReviewSessionInvitee",
            {
                "name": invitee["name"],
                "email": invitee["email"],
                "review_session": review_session
            }
        )

    # Add all objects to new review session.
    for obj in entity["review_session_objects"]:
        session.create(
            "ReviewSessionObject",
            {
                "name": obj["name"],
                "version": obj["version"],
                "review_session": review_session,
                "asset_version": obj["asset_version"]
            }
        )

    session.commit()


class CloneReviewSession(BaseAction):
    '''Generate Client Review action
    `label` a descriptive string identifing your action.
    `varaint` To group actions together, give them the same
    label and specify a unique variant per action.
    `identifier` a unique identifier for your action.
    `description` a verbose descriptive text for you action
     '''
    label = "Clone Review Session"
    variant = None
    identifier = "clone-review-session"
    description = None

    def discover(self, session, entities, event):
        '''Return true if we can handle the selected entities.
        *session* is a `ftrack_api.Session` instance
        *entities* is a list of tuples each containing the entity type and the
        entity id.
        If the entity is a hierarchical you will always get the entity
        type TypedContext, once retrieved through a get operation you
        will have the "real" entity type ie. example Shot, Sequence
        or Asset Build.
        *event* the unmodified original event
        '''
        if len(entities) == 1:
            if entities[0].entity_type == "ReviewSession":
                return True

        return False

    def launch(self, session, entities, event):
        '''Callback method for the custom action.
        return either a bool ( True if successful or False if the action
        failed ) or a dictionary with they keys `message` and `success`, the
        message should be a string and will be displayed as feedback to the
        user, success should be a bool, True if successful or False if the
        action failed.
        *session* is a `ftrack_api.Session` instance
        *entities* is a list of tuples each containing the entity type and the
        entity id.
        If the entity is a hierarchical you will always get the entity
        type TypedContext, once retrieved through a get operation you
        will have the "real" entity type ie. example Shot, Sequence
        or Asset Build.
        *event* the unmodified original event
        '''
        userId = event['source']['user']['id']
        user = session.query('User where id is ' + userId).one()
        job = session.create(
            'Job',
            {
                'user': user,
                'status': 'running',
                'data': json.dumps({
                    'description': 'Cloning Review Session.'
                })
            }
        )
        session.commit()

        try:
            clone_review_session(session, entities[0])

            job['status'] = 'done'
            session.commit()
        except Exception:
            session.rollback()
            job["status"] = "failed"
            session.commit()
            self.log.error(
                "Cloning review session failed ({})", exc_info=True
            )

        return {
            'success': True,
            'message': 'Action completed successfully'
        }


def register(session, plugins_presets=None):
    '''Register action. Called when used as an event plugin.'''

    CloneReviewSession(session, plugins_presets).register()


if __name__ == "__main__":
    import ftrack_api
    session = ftrack_api.Session()
    id = "8394ad42-4f61-11eb-9060-aecad24e2bb7"
    entity = session.get("ReviewSession", id)
    clone_review_session(session, entity)
