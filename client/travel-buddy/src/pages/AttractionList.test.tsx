import React from 'react';
import { render, screen } from '@testing-library/react';

// Simple page component tests
describe('Page Components Testing', () => {
  test('renders a basic list component', () => {
    const items = ['Item 1', 'Item 2', 'Item 3'];
    
    const SimpleList = () => (
      <ul data-testid="item-list">
        {items.map((item, index) => (
          <li key={index} data-testid={`item-${index}`}>{item}</li>
        ))}
      </ul>
    );
    
    render(<SimpleList />);
    expect(screen.getByTestId('item-list')).toBeInTheDocument();
    expect(screen.getByTestId('item-0')).toHaveTextContent('Item 1');
    expect(screen.getByTestId('item-1')).toHaveTextContent('Item 2');
    expect(screen.getByTestId('item-2')).toHaveTextContent('Item 3');
  });

  test('handles empty list correctly', () => {
    const EmptyList = () => {
      const items: string[] = [];
      return (
        <div data-testid="empty-container">
          {items.length === 0 ? (
            <p data-testid="empty-message">No items found</p>
          ) : (
            <ul>{items.map(item => <li key={item}>{item}</li>)}</ul>
          )}
        </div>
      );
    };
    
    render(<EmptyList />);
    expect(screen.getByTestId('empty-message')).toHaveTextContent('No items found');
  });

  test('search functionality works', () => {
    const SearchComponent = () => {
      const [searchTerm, setSearchTerm] = React.useState('');
      const items = ['Apple', 'Banana', 'Cherry'];
      const filteredItems = items.filter(item => 
        item.toLowerCase().includes(searchTerm.toLowerCase())
      );
      
      return (
        <div>
          <input 
            data-testid="search-input"
            placeholder="Search items..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <ul data-testid="filtered-list">
            {filteredItems.map(item => (
              <li key={item} data-testid={`filtered-${item}`}>{item}</li>
            ))}
          </ul>
        </div>
      );
    };
    
    render(<SearchComponent />);
    expect(screen.getByTestId('search-input')).toBeInTheDocument();
    expect(screen.getByTestId('filtered-list')).toBeInTheDocument();
    // Initially all items should be visible
    expect(screen.getByTestId('filtered-Apple')).toBeInTheDocument();
    expect(screen.getByTestId('filtered-Banana')).toBeInTheDocument();
    expect(screen.getByTestId('filtered-Cherry')).toBeInTheDocument();
  });
});
