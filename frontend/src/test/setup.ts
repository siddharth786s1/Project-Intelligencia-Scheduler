import '@testing-library/jest-dom';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Automatically unmount React components after each test
afterEach(() => {
  cleanup();
});
