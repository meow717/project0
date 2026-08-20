import { DashboardOverview, StaffGuard } from "@/features/dashboard";

export default function DashboardPage() {
  return (
    <StaffGuard>
      <DashboardOverview />
    </StaffGuard>
  );
}
