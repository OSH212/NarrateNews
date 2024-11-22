export function LoadingSkeleton() {
    return (
      <div className="space-y-6 w-full max-w-4xl mx-auto p-8">
        <div className="h-8 bg-muted rounded-lg w-1/3 animate-pulse" />
        
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-card rounded-lg p-6 shadow-sm">
              <div className="space-y-4">
                <div className="h-6 bg-muted rounded w-3/4 animate-pulse" />
                <div className="h-4 bg-muted rounded w-1/4 animate-pulse" />
                <div className="space-y-2">
                  <div className="h-4 bg-muted rounded animate-pulse" />
                  <div className="h-4 bg-muted rounded animate-pulse" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }