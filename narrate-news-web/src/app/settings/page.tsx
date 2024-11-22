import SettingsContent from "@/components/SettingsContent";

export default function SettingsPage() {
  return (
    <div className="flex flex-col items-center w-full px-4 md:px-8 lg:px-12 ml-[280px]">
      <div className="w-full max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">NarrateNews</h1>
        <div className="w-full">
          <SettingsContent />
        </div>
      </div>
    </div>
  );
}
