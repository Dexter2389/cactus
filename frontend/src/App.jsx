import React, { useEffect, Suspense } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoadingSpinner from "./LoadingSpinner";
import { SummarizeVideo } from "./SummarizeVideo";
import { useGetVideos } from "./apiHooks";
import { ErrorBoundary } from "./ErrorBoundary";
import ErrorFallback from "./ErrorFallback";
import apiConfig from "./apiConfig";
import './App.css'

function App() {
  const { data: videos, refetch: refetchVideos } = useGetVideos(apiConfig.INDEX_ID);
  const queryClient = useQueryClient();

  useEffect(() => {
    queryClient.invalidateQueries([apiConfig.VIDEOS, apiConfig.INDEX_ID]);
  }, [apiConfig.INDEX_ID, queryClient]);

  return (
    <Router>
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<div className="app">
              {!videos?.data && <ErrorFallback error={videos} />}
              {videos?.data && (
                <SummarizeVideo
                  index={apiConfig.INDEX_ID}
                  videoId={videos.data[0]?._id || null}
                  refetchVideos={refetchVideos}
                />
              )}
            </div>} />
            <Route path="/login" element={(<></>)} />
            <Route path="/response" element={(<></>)} />
            {/* Add more Route components here for different paths */}
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </Router>
  );
}

export default App;