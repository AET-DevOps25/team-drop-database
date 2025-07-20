import React from 'react';
import { render, screen } from '@testing-library/react';

// Simple component tests
describe('Component Testing Basics', () => {
  test('Material-UI Button renders correctly', () => {
    const TestButton = () => (
      <button data-testid="test-button">Test Button</button>
    );
    
    render(<TestButton />);
    expect(screen.getByTestId('test-button')).toBeInTheDocument();
    expect(screen.getByText('Test Button')).toBeInTheDocument();
  });

  test('Component state management works', () => {
    const TestComponent = () => {
      const [isVisible, setIsVisible] = React.useState(false);
      
      return (
        <div>
          {isVisible && <span data-testid="visible-text">Now you see me!</span>}
          <button 
            data-testid="toggle-button"
            onClick={() => setIsVisible(!isVisible)}
          >
            Toggle
          </button>
        </div>
      );
    };
    
    render(<TestComponent />);
    expect(screen.queryByTestId('visible-text')).not.toBeInTheDocument();
    expect(screen.getByTestId('toggle-button')).toBeInTheDocument();
  });

  test('Component props work correctly', () => {
    interface TestProps {
      title: string;
      count: number;
    }
    
    const TestComponent: React.FC<TestProps> = ({ title, count }) => (
      <div>
        <h1 data-testid="title">{title}</h1>
        <span data-testid="count">{count}</span>
      </div>
    );
    
    render(<TestComponent title="Test Title" count={42} />);
    expect(screen.getByTestId('title')).toHaveTextContent('Test Title');
    expect(screen.getByTestId('count')).toHaveTextContent('42');
  });
});
