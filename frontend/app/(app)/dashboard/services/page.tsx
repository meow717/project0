import { ServiceManager, StaffGuard } from "@/features/dashboard";

export default function DashboardServicesPage() {
  return (
    <StaffGuard>
      <ServiceManager />
    </StaffGuard>
  );
}
