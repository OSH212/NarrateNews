'use client';

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useState, useEffect } from "react";
import * as api from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";
import { Skeleton } from "@/components/ui/skeleton";
import { PlayIcon, PauseIcon, ExternalLinkIcon, CalendarIcon } from "@radix-ui/react-icons";
import { format } from "date-fns";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { useInView } from 'react-intersection-observer';

const LoadingSkeleton = () => (
  <div className="space-y-4">
    {[1, 2, 3].map((i) => (
      <div key={i} className="bg-card rounded-lg p-6 shadow-sm animate-pulse">
        <div className="space-y-4">
          <div className="h-6 bg-muted rounded w-3/4"></div>
          <div className="h-4 bg-muted rounded w-1/4"></div>
          <div className="space-y-2">
            <div className="h-4 bg-muted rounded"></div>
            <div className="h-4 bg-muted rounded"></div>
          </div>
        </div>
      </div>
    ))}
  </div>
);

export default function LibraryContent() {
  const [summaries, setSummaries] = useState<{ [key: string]: api.Summary }>({});
  const [loading, setLoading] = useState(true);
  const [playing, setPlaying] = useState<string | null>(null);
  const [date, setDate] = useState<Date>(new Date());
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
  const { toast } = useToast();
  const [visibleItems, setVisibleItems] = useState(10);
  const { ref, inView } = useInView();

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      loadSummaries();
    }, 300); // 300ms debounce

    return () => clearTimeout(timeoutId);
  }, [date]); // Only reload when date changes

  useEffect(() => {
    return () => {
      if (audio) {
        audio.pause();
        audio.src = "";
      }
    };
  }, [audio]);

  useEffect(() => {
    if (inView) {
      setVisibleItems(prev => prev + 10);
    }
  }, [inView]);

  const loadSummaries = async () => {
    try {
      setLoading(true);
      const fetchedSummaries = await api.getSummaries();
      const dateStr = format(date, 'yyyy-MM-dd');
      const filteredSummaries: typeof fetchedSummaries = {};
      
      Object.entries(fetchedSummaries)
        .filter(([_, summary]) => {
          const summaryDate = new Date(summary.article.publish_date);
          return format(summaryDate, 'yyyy-MM-dd') === dateStr;
        })
        .sort(([_, a], [__, b]) => {
          return new Date(b.article.publish_date).getTime() - 
                 new Date(a.article.publish_date).getTime();
        })
        .forEach(([key, summary]) => {
          filteredSummaries[key] = summary;
        });
      
      setSummaries(filteredSummaries);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load summaries. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePlayPause = (audioPath: string) => {
    if (playing === audioPath) {
      audio?.pause();
      setPlaying(null);
    } else {
      if (audio) {
        audio.pause();
      }
      const newAudio = new Audio(`http://localhost:8000${audioPath}`);
      newAudio.play().catch((error) => {
        console.error('Error playing audio:', error);
        toast({
          title: "Error",
          description: "Failed to play audio. Please try again.",
          variant: "destructive",
        });
      });
      setAudio(newAudio);
      setPlaying(audioPath);
    }
  };

  if (loading) {
    return <LoadingSkeleton />;
  }

  const summaryList = Object.values(summaries);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold"></h2>
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant={"outline"}
              className={cn(
                "w-[240px] justify-start text-left font-normal",
                !date && "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {date ? format(date, "PPP") : <span>Pick a date</span>}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="end">
            <Calendar
              mode="single"
              selected={date}
              onSelect={(newDate) => newDate && setDate(newDate)}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>

      <ScrollArea className="w-full">
        <div className="space-y-8">
          {summaryList.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No articles found for this date.
            </p>
          ) : (
            summaryList.slice(0, visibleItems).map((summary, index) => (
              <div key={summary.article.url} className="bg-card rounded-lg p-6 shadow-sm">
                <div className="space-y-4">
                  <div className="flex items-start gap-4">
                    <Button
                      variant="outline"
                      size="icon"
                      className="shrink-0 mt-1"
                      onClick={() => handlePlayPause(summary.audio_path)}
                    >
                      {playing === summary.audio_path ? (
                        <PauseIcon className="h-4 w-4" />
                      ) : (
                        <PlayIcon className="h-4 w-4" />
                      )}
                    </Button>
                    <div className="flex-1 space-y-2">
                      <h3 className="text-xl font-semibold">{summary.article.title}</h3>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <time>
                          {format(new Date(summary.article.publish_date), "PPP")}
                        </time>
                        <a
                          href={summary.article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center hover:text-primary transition-colors"
                        >
                          Read Original <ExternalLinkIcon className="ml-1 h-4 w-4" />
                        </a>
                      </div>
                    </div>
                  </div>
                  <p className="text-base leading-relaxed">{summary.summary}</p>
                </div>
                {index < summaryList.length - 1 && <Separator className="mt-8" />}
              </div>
            ))
          )}
        </div>
      </ScrollArea>
      <div ref={ref} className="h-10" />
    </div>
  );
}
