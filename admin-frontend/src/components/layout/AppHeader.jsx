import { useLocation } from 'react-router-dom';
import { NAV_ITEMS } from '../../constants/nav';
import { NavIcon } from '../icons/Icons';

function matchNavItem(pathname) {
  const p = pathname.replace(/\/$/, '') || '/';
  return NAV_ITEMS.find((item) => {
    if (item.path === '/') return p === '/' || p === '';
    return p === item.path;
  });
}

export default function AppHeader() {
  const { pathname } = useLocation();
  const item = matchNavItem(pathname);
  const label = item?.label ?? 'Config Manager';

  return (
    <header className="flex shrink-0 items-center gap-3 border-b border-gray-200 bg-white px-6 py-4">
      {item && <NavIcon name={item.icon} className="h-6 w-6 text-brand-red" />}
      <h1 className="text-lg font-semibold tracking-tight text-gray-900">{label}</h1>
    </header>
  );
}
