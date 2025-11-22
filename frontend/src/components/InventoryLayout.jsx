import { Navigation } from './Navigation';
import './InventoryLayout.css';

export function InventoryLayout({ children }) {
  return (
    <div className="inventory-layout">
      <Navigation />
      <main className="inventory-main">
        {children}
      </main>
    </div>
  );
}
