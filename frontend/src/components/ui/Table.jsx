import './Table.css';

export function Table({ children, className = '', ...props }) {
  return (
    <div className="table-container">
      <table className={`table ${className}`} {...props}>
        {children}
      </table>
    </div>
  );
}

export function TableHeader({ children, className = '', ...props }) {
  return (
    <thead className={`table-header ${className}`} {...props}>
      {children}
    </thead>
  );
}

export function TableBody({ children, className = '', ...props }) {
  return (
    <tbody className={`table-body ${className}`} {...props}>
      {children}
    </tbody>
  );
}

export function TableFooter({ children, className = '', ...props }) {
  return (
    <tfoot className={`table-footer ${className}`} {...props}>
      {children}
    </tfoot>
  );
}

export function TableRow({ children, className = '', ...props }) {
  return (
    <tr className={`table-row ${className}`} {...props}>
      {children}
    </tr>
  );
}

export function TableHead({ children, className = '', ...props }) {
  return (
    <th className={`table-head ${className}`} {...props}>
      {children}
    </th>
  );
}

export function TableCell({ children, className = '', ...props }) {
  return (
    <td className={`table-cell ${className}`} {...props}>
      {children}
    </td>
  );
}

export function TableCaption({ children, className = '', ...props }) {
  return (
    <caption className={`table-caption ${className}`} {...props}>
      {children}
    </caption>
  );
}
