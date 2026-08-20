import { BusinessCreateForm, StaffGuard } from "@/features/dashboard";

export default function DashboardBusinessPage() {
  return (
    <StaffGuard>
      <BusinessCreateForm />
    </StaffGuard>
  );
}
