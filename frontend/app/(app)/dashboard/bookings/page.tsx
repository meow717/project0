import { BookingsManage, StaffGuard } from "@/features/dashboard";

export default function DashboardBookingsPage() {
  return (
    <StaffGuard>
      <BookingsManage />
    </StaffGuard>
  );
}
