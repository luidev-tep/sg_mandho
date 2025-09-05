import * as React from "react"
import { format } from "date-fns"

import { cn } from "../lib/utils"

export default function DatePickerWithRange({
  className,
}) {
  const currentDate = new Date()

  return (
    <div className={cn("grid gap-4", className)}>
      <div
        className={cn(
          "btn px-3 min-w-[15.5rem] bg-white border-gray-200 dark:border-gray-700/60 dark:bg-gray-800 text-gray-600 dark:text-gray-300 font-medium text-left justify-start flex items-center"
        )}
      >
        <svg className="fill-current text-gray-400 dark:text-gray-500 ml-1 mr-2" width="16" height="16" viewBox="0 0 16 16">
          <path d="M5 4a1 1 0 0 0 0 2h6a1 1 0 1 0 0-2H5Z"></path>
          <path d="M4 0a4 4 0 0 0-4 4v8a4 4 0 0 0 4 4h8a4 4 0 0 0 4-4V4a4 4 0 0 0-4-4H4ZM2 4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4Z"></path>
        </svg>
        {format(currentDate, "yyyy-MMM-dd")}
      </div>
    </div>
  )
}