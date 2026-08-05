import Download from "@/components/Download";
import Footer from "@/components/Footer";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import TodaysIssues from "@/components/TodaysIssues";

export default function Home() {
  return (
    <>
      <Header />

      <Hero />

      <Download />

      <TodaysIssues />

      <Footer />
    </>
  );
}