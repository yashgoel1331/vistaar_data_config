export const NAV_ITEMS = [
  { key: 'glossary',        label: 'Glossary',            path: '/',               icon: 'book' },
  { key: 'ambiguous-terms', label: 'Ambiguous Terms',    path: '/ambiguity',      icon: 'help' },
  { key: 'aliases-en-gu',   label: 'Aliases (en-gu)',    path: '/aliases/en-gu',  icon: 'translate' },
  { key: 'aliases-english', label: 'Aliases (english)',  path: '/aliases/english', icon: 'file' },
  { key: 'forbidden',       label: 'Forbidden',         path: '/forbidden',      icon: 'ban' },
  { key: 'preferred',       label: 'Preferred',         path: '/preferred',      icon: 'star' },
  { key: 'schemes',         label: 'Schemes',           path: '/schemes',        icon: 'link' },
  { key: 'config',          label: 'Config Management', path: '/config',         icon: 'settings' },
];

export const CONFIG_TYPE_OPTIONS = [
  { value: 'glossary',            label: 'Glossary' },
  { value: 'ambiguous_terms',     label: 'Ambiguous Terms' },
  { value: 'en-gujarati_aliases', label: 'Aliases (en-gu)' },
  { value: 'english_aliases',     label: 'Aliases (english)' },
  { value: 'forbidden',           label: 'Forbidden' },
  { value: 'preferred',           label: 'Preferred' },
  { value: 'schemes',             label: 'Schemes' },
];
