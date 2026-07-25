import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'TrustTrace | AI Behavioral Anomaly Detection',
  description:
    'Real-time AI-powered behavioral anomaly detection for cybersecurity — detect intrusions, compromised credentials, and lateral movement.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Sidebar />
        <main className="main-content">{children}</main>
      </body>
    </html>
  );
}
