import React from "react";
import { Button } from "./ui/button";

export function ColorTest() {
  return (
    <div className="p-8 space-y-6">
      <h2 className="text-2xl font-bold">Color Test Component</h2>
      
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Background Color Classes</h3>
        <div className="flex space-x-4">
          <div className="bg-primary text-primary-foreground p-4 rounded-md">
            bg-primary
          </div>
          <div className="bg-secondary text-secondary-foreground p-4 rounded-md">
            bg-secondary
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Button Variants</h3>
        <div className="flex space-x-4">
          <Button variant="default">Primary Button (default)</Button>
          <Button variant="secondary">Secondary Button</Button>
          <Button variant="outline">Outline Button</Button>
        </div>
      </div>
    </div>
  );
}