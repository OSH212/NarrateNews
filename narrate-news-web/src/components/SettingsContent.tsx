"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import * as api from "@/lib/api";
import { Check, ChevronsUpDown } from "lucide-react"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem } from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { cn } from "@/lib/utils"

interface Voice {
  id: string;
  name: string;
}

interface Settings {
  ttsProvider: string;
  voice: string;
  neetModel: string;
  summarizerModel: string;
  rssFeeds: string[];
  autoPlay: boolean;
  processInterval: number;
}

export default function SettingsContent() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [voices, setVoices] = useState<Voice[]>([]);
  const [loading, setLoading] = useState(true);
  const [newFeed, setNewFeed] = useState("");
  const { toast } = useToast();
  const [updating, setUpdating] = useState(false);
  const [modelHistory, setModelHistory] = useState<string[]>([
    "openrouter/google/gemini-flash-1.5", // Default from config.py
  ]);
  const [openModelSelect, setOpenModelSelect] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  useEffect(() => {
    if (settings?.ttsProvider) {
      loadVoices(settings.ttsProvider);
    }
  }, [settings?.ttsProvider]);

  useEffect(() => {
    const savedHistory = localStorage.getItem('modelHistory');
    if (savedHistory) {
      setModelHistory(JSON.parse(savedHistory));
    }
  }, []);

  const loadSettings = async () => {
    try {
      const settings = await api.getSettings();
      setSettings(settings);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load settings",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadVoices = async (provider: string) => {
    try {
      const voices = await api.getVoices(provider);
      setVoices(voices);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load voices",
        variant: "destructive",
      });
    }
  };

  const handleSettingChange = async (key: keyof Settings, value: any) => {
    if (!settings || updating) return;

    // Optimistically update UI
    setSettings(prev => prev ? { ...prev, [key]: value } : null);
    
    try {
      await api.updateSettings({ ...settings, [key]: value });
      toast({
        title: "Success",
        description: "Settings updated successfully",
      });
    } catch (error) {
      // Revert on error
      setSettings(settings);
      toast({
        title: "Error",
        description: "Failed to update settings",
        variant: "destructive",
      });
    }
  };

  const handleAddFeed = async () => {
    if (!settings || !newFeed) return;

    const feeds = [...settings.rssFeeds, newFeed];
    await handleSettingChange("rssFeeds", feeds);
    setNewFeed("");
  };

  const handleRemoveFeed = async (feed: string) => {
    if (!settings) return;

    const feeds = settings.rssFeeds.filter((f) => f !== feed);
    await handleSettingChange("rssFeeds", feeds);
  };

  const handleProcessFeeds = async () => {
    try {
      await api.startProcessing();
      toast({
        title: "Success",
        description: "Started processing feeds.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to start processing",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (!settings) {
    return null;
  }

  return (
    <div className="space-y-6 w-full max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Process Feeds</CardTitle>
          <CardDescription>Start processing RSS feeds to generate summaries and audio</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={handleProcessFeeds}>Process Feeds</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>RSS Feeds</CardTitle>
          <CardDescription>Manage your news sources</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex space-x-2">
              <Input
                placeholder="Enter RSS feed URL"
                value={newFeed}
                onChange={(e) => setNewFeed(e.target.value)}
              />
              <Button onClick={handleAddFeed}>Add Feed</Button>
            </div>
            <div className="space-y-2">
              {settings.rssFeeds.map((feed) => (
                <div key={feed} className="flex justify-between items-center">
                  <span className="truncate">{feed}</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleRemoveFeed(feed)}
                  >
                    Remove
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Text-to-Speech Settings</CardTitle>
          <CardDescription>Configure voice synthesis options</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Provider</Label>
            <Select
              value={settings.ttsProvider}
              onValueChange={(value) => handleSettingChange("ttsProvider", value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select provider" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="elevenlabs">ElevenLabs</SelectItem>
                <SelectItem value="neets">Neets</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Voice</Label>
            <Select
              value={settings.voice}
              onValueChange={(value) => handleSettingChange("voice", value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select voice" />
              </SelectTrigger>
              <SelectContent>
                {voices.map((voice) => (
                  <SelectItem key={voice.id} value={voice.id}>
                    {voice.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {settings.ttsProvider === "neets" && (
            <div className="space-y-2">
              <Label>Neets Model</Label>
              <Select
                value={settings.neetModel}
                onValueChange={(value) => handleSettingChange("neetModel", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="v2">V2</SelectItem>
                  <SelectItem value="v2.1">V2.1</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>AI Model Settings</CardTitle>
          <CardDescription>Configure text summarization</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label>Summarizer Model</Label>
            <Popover open={openModelSelect} onOpenChange={setOpenModelSelect}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  role="combobox"
                  aria-expanded={openModelSelect}
                  className="w-full justify-between"
                >
                  {settings.summarizerModel}
                  <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-full p-0">
                <Command>
                  <CommandInput placeholder="Search model or enter new..." />
                  <CommandEmpty>
                    <div className="px-4 py-2">
                      <p>No model found. Press enter to add new model.</p>
                      <Button 
                        variant="ghost" 
                        className="mt-2"
                        onClick={() => {
                          const input = document.querySelector('[cmdk-input]') as HTMLInputElement;
                          const newModel = input?.value;
                          if (newModel && !modelHistory.includes(newModel)) {
                            setModelHistory(prev => [...prev, newModel]);
                            handleSettingChange("summarizerModel", newModel);
                            setOpenModelSelect(false);
                          }
                        }}
                      >
                        Add and select model
                      </Button>
                    </div>
                  </CommandEmpty>
                  <CommandGroup>
                    {modelHistory.map((model) => (
                      <CommandItem
                        key={model}
                        onSelect={() => {
                          handleSettingChange("summarizerModel", model);
                          setOpenModelSelect(false);
                        }}
                      >
                        <Check
                          className={cn(
                            "mr-2 h-4 w-4",
                            settings.summarizerModel === model ? "opacity-100" : "opacity-0"
                          )}
                        />
                        {model}
                      </CommandItem>
                    ))}
                  </CommandGroup>
                </Command>
              </PopoverContent>
            </Popover>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Playback Settings</CardTitle>
          <CardDescription>Configure audio playback behavior</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <Switch
              checked={settings.autoPlay}
              onCheckedChange={(checked) => handleSettingChange("autoPlay", checked)}
            />
            <Label>Auto-play next article</Label>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Processing Settings</CardTitle>
          <CardDescription>Configure article processing behavior</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label>Processing Interval (seconds)</Label>
            <Input
              type="number"
              value={settings.processInterval}
              onChange={(e) => handleSettingChange("processInterval", parseInt(e.target.value))}
              min={60}
              max={3600}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
