import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Test from './Test';

describe('Test component', () => {
  it('renders the default greeting', () => {
    render(<Test />);
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });

  it('updates the greeting when the input changes', () => {
    render(<Test />);
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Shalom' } });
    expect(screen.getByText('Shalom')).toBeInTheDocument();
  });
});
