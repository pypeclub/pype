module.exports = {
  title: 'PYPE',
  tagline: 'code . training . support',
  url: 'http://pype.club/',
  baseUrl: 'pype/',
  organizationName: 'pypeclub',
  projectName: 'pype',
  favicon: 'img/favicon/favicon.ico',
  onBrokenLinks: 'ignore',
  customFields: {
  },
  presets: [
    [
      '@docusaurus/preset-classic', {
        docs: {
          sidebarPath: require.resolve('./pype/sidebars.js'),
        },
        theme: {
          customCss: require.resolve('./pype/src/css/custom.css')
        }
      }
    ]
  ],
  themeConfig: {
    colorMode: {
      // "light" | "dark"
      defaultMode: 'light',

      // Hides the switch in the navbar
      // Useful if you want to support a single color mode
      disableSwitch: true
    },
    navbar: {
      style: 'dark',
      title: 'PYPE',
      logo: {
        src: 'img/favicon/P.png'
      },
      items: [
        {
          to: '/features',
          label: 'Features',
          position: 'left'
        }, {
          to: 'docs/artist_getting_started',
          label: 'User Docs',
          position: 'left'
        },{
          to: 'docs/admin_getting_started',
          label: 'Admin Docs',
          position: 'left'
        }, {
          to: 'docs/api',
          label: 'API',
          position: 'left'
        }
      ]
    },
    image: '/img/docusaurus.png',
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Artist',
              to: 'pype/docs/artist_getting_started',
            },
            {
              label: 'Manager',
              to: 'pype/docs/manager_ftrack',
            },
            {
              label: 'Admin',
              to: 'pype/docs/admin_config',
            },
          ],
        },{
          title: 'Social',
          items: [
            {
              label: 'Avalon Chat',
              to: 'https://gitter.im/getavalon/Lobby',
            },
            {
              label: 'Pyblish Chat',
              to: 'https://gitter.im/pyblish/pyblish',
            },
            {
              label: 'Pype Chat',
              to: 'https://discord.gg/sFNPWXG',
            },
          ],
        },
      ],
      copyright: 'Copyright © 2020 Orbi Tools',
    },
    algolia: {
      apiKey: '5e01ee3bfbb744ca6f25d4b281ce38a9',
      indexName: 'pype',
      algoliaOptions: {}
    }
  },
  stylesheets: [
        'https://use.fontawesome.com/releases/v5.7.2/css/all.css'
    ],
};
