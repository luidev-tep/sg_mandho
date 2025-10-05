import React, { useState } from 'react';

function SidebarLinkGroup({
  children,
  activecondition,
  alwaysOpen = false, // Nueva propiedad para mantener el grupo abierto
}) {

  const [open, setOpen] = useState(alwaysOpen || activecondition);

  const handleClick = () => {
    // Solo permite cerrar si no está configurado para estar siempre abierto
    if (!alwaysOpen) setOpen(!open);
  }

  return (
    <li className={`pl-4 pr-3 py-2 rounded-lg mb-0.5 last:mb-0 bg-linear-to-r ${activecondition && 'from-violet-500/[0.12] dark:from-violet-500/[0.24] to-violet-500/[0.04]'}`}>
      {children(handleClick, open)}
    </li>
  );
}

export default SidebarLinkGroup; 