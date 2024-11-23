'use client';

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { 
  PlayCircle, 
  PauseCircle, 
  SkipForward, 
  SkipBack, 
  Repeat,
} from "lucide-react";
import { CalendarIcon } from "@radix-ui/react-icons";
import { format } from "date-fns";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import * as api from "@/lib/api";
import { createPollingFunction } from "@/lib/api";

export default function PlayerContent() {
  const [summaries, setSummaries] = useState<api.Summary[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [autoPlay, setAutoPlay] = useState(false);
  const [date, setDate] = useState<Date>(new Date());
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const stopPolling = api.createPollingFunction(
      () => api.getSummaries()
    )((newSummaries) => {
      const dateStr = format(date, 'yyyy-MM-dd');
      const filteredSummaries = Object.values(newSummaries)
        .filter(summary => {
          const summaryDate = new Date(summary.article.publish_date);
          return format(summaryDate, 'yyyy-MM-dd') === dateStr;
        })
        .sort((a, b) => 
          new Date(b.article.publish_date).getTime() - 
          new Date(a.article.publish_date).getTime()
        );
      setSummaries(filteredSummaries);
    });

    return () => stopPolling();
  }, [date]); // Only recreate polling when date changes

  const playAudio = async (index: number) => {
    if (audioRef.current) {
      setIsLoading(true);
      try {
        audioRef.current.src = `http://localhost:8000${summaries[index].audio_path}`;
        await audioRef.current.play();
        setCurrentIndex(index);
        setIsPlaying(true);
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to play audio",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        if (currentIndex === -1 && summaries.length > 0) {
          playAudio(0);
        } else {
          audioRef.current.play().catch(console.error);
        }
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleNext = () => {
    if (currentIndex < summaries.length - 1) {
      playAudio(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      playAudio(currentIndex - 1);
    }
  };

  const handleEnded = () => {
    if (autoPlay && currentIndex < summaries.length - 1) {
      playAudio(currentIndex + 1);
    } else {
      setIsPlaying(false);
      setCurrentIndex(-1);
    }
  };

  const preloadAudio = (url: string) => {
    const audio = new Audio();
    audio.preload = "metadata";
    audio.src = url;
  };

  useEffect(() => {
    if (currentIndex >= 0 && currentIndex < summaries.length - 1) {
      const nextAudio = summaries[currentIndex + 1];
      preloadAudio(`http://localhost:8000${nextAudio.audio_path}`);
    }
  }, [currentIndex, summaries]);

  useEffect(() => {
    if (currentIndex >= 0 && currentIndex < summaries.length - 1) {
      const nextAudio = summaries[currentIndex + 1];
      const audio = new Audio();
      audio.preload = "metadata";
      audio.src = `http://localhost:8000${nextAudio.audio_path}`;
    }
  }, [currentIndex, summaries]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
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
        <Button
          variant="outline"
          onClick={() => setAutoPlay(!autoPlay)}
          className={autoPlay ? "bg-primary text-primary-foreground" : ""}
        >
          <Repeat className="mr-2 h-4 w-4" />
          Auto-play
        </Button>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex justify-center space-x-4">
              <Button variant="outline" size="icon" onClick={handlePrevious}>
                <SkipBack className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={handlePlayPause}>
                {isPlaying ? (
                  <PauseCircle className="h-4 w-4" />
                ) : (
                  <PlayCircle className="h-4 w-4" />
                )}
              </Button>
              <Button variant="outline" size="icon" onClick={handleNext}>
                <SkipForward className="h-4 w-4" />
              </Button>
            </div>

            {currentIndex !== -1 && (
              <div className="space-y-2">
                <h3 className="text-lg font-semibold">
                  {summaries[currentIndex].article.title}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {format(new Date(summaries[currentIndex].article.publish_date), "PPP")}
                </p>
                <p className="text-base leading-relaxed">
                  {summaries[currentIndex].summary}
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <ScrollArea className="h-[400px]">
        <div className="space-y-4">
          {summaries.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No articles found for this date.
            </p>
          ) : (
            summaries.map((summary, index) => (
              <Card
                key={summary.article.url}
                className={`p-4 cursor-pointer hover:bg-accent ${
                  index === currentIndex ? "border-primary" : ""
                }`}
                onClick={() => playAudio(index)}
              >
                <CardContent className="p-0">
                  <div className="flex items-center space-x-4">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="shrink-0"
                    >
                      {index === currentIndex && isPlaying ? (
                        <PauseCircle className="h-4 w-4" />
                      ) : (
                        <PlayCircle className="h-4 w-4" />
                      )}
                    </Button>
                    <div>
                      <h4 className="font-medium">{summary.article.title}</h4>
                      <p className="text-sm text-muted-foreground">
                        {format(new Date(summary.article.publish_date), "PPP")}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>

      <audio
        ref={audioRef}
        onEnded={handleEnded}
        onError={() => {
          toast({
            title: "Error",
            description: "Failed to play audio",
            variant: "destructive",
          });
          setIsPlaying(false);
        }}
      />
    </div>
  );
}