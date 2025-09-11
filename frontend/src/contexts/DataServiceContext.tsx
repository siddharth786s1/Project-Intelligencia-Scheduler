import React from 'react';
import { DataServiceContext } from '../services/dataService';
import DataService from '../services/dataService';

interface DataServiceProviderProps {
  children: React.ReactNode;
}

export const DataServiceProvider: React.FC<DataServiceProviderProps> = ({ children }) => {
  return (
    <DataServiceContext.Provider value={DataService}>
      {children}
    </DataServiceContext.Provider>
  );
};
