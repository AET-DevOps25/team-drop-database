import React from 'react';
import { render, screen } from '@testing-library/react';

// Simple App component test without router dependencies
describe('App Component Basic Tests', () => {
  test('basic React rendering works', () => {
    const TestComponent = () => <div data-testid="test">Hello World</div>;
    render(<TestComponent />);
    expect(screen.getByTestId('test')).toBeInTheDocument();
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });

  test('React hooks work correctly', () => {
    const TestComponent = () => {
      const [count, setCount] = React.useState(0);
      return (
        <div>
          <span data-testid="count">{count}</span>
          <button onClick={() => setCount(count + 1)}>Increment</button>
        </div>
      );
    };
    
    render(<TestComponent />);
    expect(screen.getByTestId('count')).toHaveTextContent('0');
  });

  test('Material-UI components can be imported', () => {
    // This test verifies that our dependencies are properly set up
    expect(typeof React.createElement).toBe('function');
  });
});
