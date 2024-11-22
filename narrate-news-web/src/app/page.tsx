import Image from "next/image";
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import LibraryContent from '@/components/LibraryContent';
import PlayerContent from '@/components/PlayerContent';

export default function Home() {
  return (
    <div className="flex flex-col items-center w-full px-4 md:px-8 lg:px-12 ml-[230px]">
      <div className="w-full max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">NarrateNews</h1>
        <main className="w-full">
          <Tabs defaultValue="library" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="library">Library</TabsTrigger>
              <TabsTrigger value="player">Player</TabsTrigger>
            </TabsList>
            <TabsContent value="library">
              <LibraryContent />
            </TabsContent>
            <TabsContent value="player">
              <PlayerContent />
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  );
}
