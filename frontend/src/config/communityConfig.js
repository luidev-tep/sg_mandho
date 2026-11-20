// Identidad y catálogos públicos de la comunidad.
export const communityConfig = {
  branding: { appName: 'S.G. Comunitario — El Mandhó', shortName: 'S.G. El Mandhó', tagline: 'Sistema de gestión comunitaria para el futuro', location: 'Ixmiquilpan, Hidalgo', website: 'sgmandho.com.mx', logoInitials: 'SG' },
  geography: { zoneLabel: 'Manzana', zoneLabelPlural: 'Manzanas', zones: [
    { value: 'tepetate', label: 'Tepetate' }, { value: 'cerritos', label: 'Cerritos' },
    { value: 'garambullo', label: 'Garambullo' }, { value: 'yhonda', label: 'Yhonda' },
    { value: 'centro', label: 'Centro' }, { value: 'buenavista', label: 'Buena Vista' },
  ] },
  governance: { roles: { delegado: 'Delegado', subdelegado: 'Subdelegado', comitiva: 'Comitiva', vecino: 'Vecino' } },
  services: { agua: { name: 'Agua', label: 'Agua', route: '/modulos/agua' }, feria: { name: 'Feria', label: 'Feria', route: '/modulos/feria' }, panteon: { name: 'Panteón', label: 'Panteón', route: '/modulos/panteon' }, delegacion: { name: 'Delegación', label: 'Delegación', route: '/modulos/delegacion' } },
};
export default communityConfig;
