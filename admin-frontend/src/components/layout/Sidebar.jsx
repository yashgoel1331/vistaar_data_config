import { NavLink } from 'react-router-dom';
import { NAV_ITEMS } from '../../constants/nav';
import { NavIcon } from '../icons/Icons';

export default function Sidebar() {
  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-5 py-5">
        <span className="text-base font-bold tracking-tight text-gray-900">Config Manager</span>
      </div>
      <nav className="flex-1 space-y-0.5 overflow-y-auto p-3">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-brand-redlight text-brand-red'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <NavIcon
                  name={item.icon}
                  className={`h-5 w-5 shrink-0 ${isActive ? 'text-brand-red' : 'text-gray-500'}`}
                />
                <span>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
