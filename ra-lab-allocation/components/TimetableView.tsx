'use client'

import React, { useMemo } from 'react'
import { Allocation, SlotMap } from '@/lib/types'
import { scheduleData } from '@/lib/schedule'

interface TimetableViewProps {
  allocations: Allocation[]
  slotMap: SlotMap
  selectedRA: string | null
}

const days = ['MON', 'TUE', 'WED', 'THU', 'FRI'];

// Header Data
const theoryMorning = [
  "8:00 AM to 8:50 AM", "9:00 AM to 9:50 AM", "10:00 AM to 10:50 AM",
  "11:00 AM to 11:50 AM", "12:00 PM to 12:50 PM", ""
];
const theoryAfternoon = [
  "2:00 PM to 2:50 PM", "3:00 PM to 3:50 PM", "4:00 PM to 4:50 PM",
  "5:00 PM to 5:50 PM", "6:00 PM to 6:50 PM", "6:51 PM to 7:00 PM", "7:01 PM to 7:50 PM"
];

const labMorning = [
  "08:00 AM to 08:50 AM", "08:51 AM to 09:40 AM", "09:51 AM to 10:40 AM",
  "10:41 AM to 11:30 AM", "11:40 AM to 12:30 PM", "12:31 PM to 1:20 PM"
];
const labAfternoon = [
  "2:00 PM to 2:50 PM", "2:51 PM to 3:40 PM", "3:51 PM to 4:40 PM",
  "4:41 PM to 5:30 PM", "5:40 PM to 6:30 PM", "6:31 PM to 7:20 PM", ""
];

export default function TimetableView({ allocations, selectedRA }: TimetableViewProps) {

  const filteredAllocations = useMemo(() => {
    if (!selectedRA) {
      return allocations;
    }
    return allocations.filter(a => a.raName === selectedRA);
  }, [allocations, selectedRA]);

  const allocationMap = useMemo(() => {
    const map = new Map<string, Allocation>();
    filteredAllocations.forEach(alloc => {
      const labSlots = (alloc.slot || '').split('+').map(s => s.trim());
      labSlots.forEach(labSlot => {
        map.set(labSlot, alloc);
      });
    });
    return map;
  }, [filteredAllocations]);

  const renderCell = (day: string, slotIndex: number) => {
    const daySchedule = scheduleData.SCHEDULE[day as keyof typeof scheduleData.SCHEDULE];
    // slotIndex maps to the schedule array. 
    // Morning: 0-5. Afternoon: 7-13. (Index 6 is Lunch)
    const scheduleSlot = daySchedule[slotIndex];

    if (!scheduleSlot) return <td className="border border-gray-400 bg-yellow-50"></td>;

    const allocation = scheduleSlot.lab ? allocationMap.get(scheduleSlot.lab) : undefined;
    const isAllocated = !!allocation;

    return (
      <td className={`border border-gray-400 p-1 text-center align-middle h-16 w-32 ${isAllocated ? 'bg-green-100' : 'bg-yellow-50'}`}>
        <div className="flex flex-col items-center justify-center h-full w-full">
          {/* Base Slot Info */}
          <div className="text-xs font-bold text-gray-700">
            {scheduleSlot.course && scheduleSlot.lab
              ? `${scheduleSlot.course} / ${scheduleSlot.lab}`
              : scheduleSlot.lab || scheduleSlot.course || '-'}
          </div>

          {/* Allocation Info Overlay */}
          {allocation && (
            <div className="mt-1 text-[10px] leading-tight text-blue-800 bg-blue-50/80 p-1 rounded w-full overflow-hidden">
              <div className="font-semibold truncate" title={allocation.courseCode}>{allocation.courseCode}</div>
              <div className="truncate" title={allocation.roomNumber}>{allocation.roomNumber}</div>
              {/* Only show RA name if we are viewing all allocations, otherwise it's redundant */}
              {!selectedRA && <div className="truncate text-purple-700 font-medium" title={allocation.raName}>{allocation.raName}</div>}
            </div>
          )}
        </div>
      </td>
    );
  };

  return (
    <div className="w-full overflow-x-auto p-4 bg-white rounded-xl shadow-sm">
      <table className="w-full border-collapse border border-gray-400 text-sm">
        <tbody>
          {/* Row 1: Theory Hours */}
          <tr className="bg-blue-200">
            <td className="border border-gray-400 p-2 font-bold text-center w-24 bg-gray-300">
              THEORY<br />HOURS
            </td>
            {theoryMorning.map((time, i) => (
              <td key={`tm-${i}`} className="border border-gray-400 p-1 text-center text-[10px] font-semibold">
                {time.replace(' to ', '<br/>to<br/>').split('<br/>').map((line, idx) => <div key={idx}>{line}</div>)}
              </td>
            ))}

            {/* LUNCH Column - Spans all rows */}
            <td rowSpan={2 + days.length} className="border border-gray-400 bg-gray-200 text-center font-bold w-8 align-middle writing-vertical">
              <div className="flex flex-col items-center justify-center h-full gap-1 py-4">
                {'LUNCH'.split('').map((char, i) => <span key={i}>{char}</span>)}
              </div>
            </td>

            {theoryAfternoon.map((time, i) => (
              <td key={`ta-${i}`} className="border border-gray-400 p-1 text-center text-[10px] font-semibold">
                {time.replace(' to ', '<br/>to<br/>').split('<br/>').map((line, idx) => <div key={idx}>{line}</div>)}
              </td>
            ))}
          </tr>

          {/* Row 2: Lab Hours */}
          <tr className="bg-blue-300">
            <td className="border border-gray-400 p-2 font-bold text-center bg-gray-300">
              LAB<br />HOURS
            </td>
            {labMorning.map((time, i) => (
              <td key={`lm-${i}`} className="border border-gray-400 p-1 text-center text-[10px] font-semibold">
                {time.replace(' to ', '<br/>to<br/>').split('<br/>').map((line, idx) => <div key={idx}>{line}</div>)}
              </td>
            ))}
            {/* Lunch column is spanned from above */}
            {labAfternoon.map((time, i) => (
              <td key={`la-${i}`} className="border border-gray-400 p-1 text-center text-[10px] font-semibold">
                {time ? time.replace(' to ', '<br/>to<br/>').split('<br/>').map((line, idx) => <div key={idx}>{line}</div>) : ''}
              </td>
            ))}
          </tr>

          {/* Data Rows */}
          {days.map((day) => (
            <tr key={day}>
              <td className="border border-gray-400 p-2 font-bold text-center bg-gray-300">
                {day}
              </td>
              {/* Morning Slots (0-5) */}
              {[0, 1, 2, 3, 4, 5].map(idx => (
                <React.Fragment key={`${day}-m-${idx}`}>
                  {renderCell(day, idx)}
                </React.Fragment>
              ))}

              {/* Lunch column is spanned */}

              {/* Afternoon Slots (7-13) */}
              {[7, 8, 9, 10, 11, 12, 13].map(idx => (
                <React.Fragment key={`${day}-a-${idx}`}>
                  {renderCell(day, idx)}
                </React.Fragment>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
