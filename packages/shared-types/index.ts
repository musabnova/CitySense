export type LifecycleStatus = 'Submitted' | 'Under Review' | 'Assigned' | 'Resolved';

export type PriorityRank = 'Priority 1' | 'Priority 2' | 'Priority 3' | 'Priority 4';

export type CivicCategory =
  | 'Waterlogging & Drainage'
  | 'Road Failure & Potholes'
  | 'Waste Management'
  | 'Street Lighting'
  | 'Public Utilities';

export interface LocationCoordinates {
  latitude: number;
  longitude: number;
  formattedAddress?: string;
}

export interface ReportItem {
  id: string;
  trackingId: string;
  createdAt: string;
  updatedAt: string;
  rawDescription: string;
  userCategory?: CivicCategory;
  verifiedCategory: CivicCategory;
  mediaUrl?: string;
  location: LocationCoordinates;
  conciseSummary?: string;
  isDuplicate: boolean;
  masterTicketId?: string | null;
  duplicateCount: number;
  priorityRank: PriorityRank;
  priorityScore: number;
  priorityRationale?: string;
  lifecycleStatus: LifecycleStatus;
  assignedDepartment?: string | null;
  dispatchTimestamp?: string | null;
  resolutionNotes?: string | null;
}

