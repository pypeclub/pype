import ftrack_api
from pype.ftrack import BaseEvent, get_ca_mongoid
from pype.ftrack.events.event_sync_to_avalon import Sync_to_Avalon


class DelAvalonIdFromNew(BaseEvent):
    '''
    This event removes AvalonId from custom attributes of new entities
    Result:
    - 'Copy->Pasted' entities won't have same AvalonID as source entity

    Priority of this event must be less than SyncToAvalon event
    '''
    priority = Sync_to_Avalon.priority - 1

    def launch(self, event):
        created = []
        entities = event['data']['entities']
        for entity in entities:
            try:
                entity_id = entity['entityId']

                if entity['action'] == 'add':
                    id_dict = entity['changes']['id']

                    if id_dict['new'] is not None and id_dict['old'] is None:
                        created.append(id_dict['new'])

                elif (
                    entity['action'] == 'update' and
                    get_ca_mongoid() in entity['keys'] and
                    entity_id in created
                ):
                    ftrack_entity = self.session.get(
                        self._get_entity_type(entity),
                        entity_id
                    )

                    cust_attr = ftrack_entity['custom_attributes'][
                        get_ca_mongoid()
                    ]

                    if cust_attr != '':
                        ftrack_entity['custom_attributes'][
                            get_ca_mongoid()
                        ] = ''
                        self.session.commit()

            except Exception:
                continue

    def register(self):
        '''Registers the event, subscribing the discover and launch topics.'''
        self.session.event_hub.subscribe(
            'topic=ftrack.update',
            self.launch,
            priority=self.priority
        )


def register(session, **kw):
    '''Register plugin. Called when used as an plugin.'''
    if not isinstance(session, ftrack_api.session.Session):
        return

    DelAvalonIdFromNew(session).register()