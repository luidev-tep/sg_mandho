import React from 'react';

function JobListItem({ id, name, role, details, date }) {
  return (
    <div
      className="bg-white dark:bg-gray-800 shadow-xs rounded-xl px-5 py-4 border border-gray-100 dark:border-gray-700 hover:border-gray-200 dark:hover:border-gray-600 transition-colors duration-200"
    >
      <div className="md:flex justify-between items-center space-y-3 md:space-y-0">
        {/* Left side */}
        <div className="flex items-start space-x-4">
          <div className="w-10 h-10 shrink-0 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
            <span className="text-lg font-medium text-gray-500 dark:text-gray-300">
              {name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h3 className="font-bold text-gray-800 dark:text-gray-100">
              {name}
            </h3>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-300">
              {role}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {details}
            </p>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4 pl-14 md:pl-0 mt-3 md:mt-0">
          <div className="text-sm text-gray-500 dark:text-gray-400 whitespace-nowrap">
            {new Date(date).toLocaleDateString('es-MX', {
              year: 'numeric',
              month: 'short',
              day: 'numeric'
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default JobListItem;