import React from "react";
import end from "./icons8-end-50.png";
import ff from "./icons8-fast-forward-50.png";
import pause from "./icons8-pause-50.png";
import play from "./icons8-play-50.png";
import rewind from "./icons8-rewind-50.png";
import skiptostart from "./icons8-skip-to-start-50.png";

interface AnimControlButtonsProps {
  paused?: boolean;
  onSkipToStart?: () => void;
  onPlay?: () => void;
  onPause?: () => void;
  onPrev?: () => void;
  onNext?: () => void;
  onEnd?: () => void;
}

const AnimControls: React.FC<AnimControlButtonsProps> = ({
  onPlay,
  onPause,
  onSkipToStart,
  onPrev,
  onNext,
  onEnd,
  paused = true,
}) => {
  const buttonStyle: React.CSSProperties = {
    background: "rgba(30, 32, 36, 0.85)",
    border: "none",
    borderRadius: "50%",
    boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
    padding: "0.5rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "background 0.2s, box-shadow 0.2s, transform 0.1s",
    cursor: "pointer",
    outline: "none",
  };

  const buttonHoverStyle: React.CSSProperties = {
    background: "rgba(60, 64, 72, 1)",
    boxShadow: "0 4px 16px rgba(0,0,0,0.25)",
    transform: "scale(1.01)",
  };

  const imgStyle: React.CSSProperties = {
    filter: "invert(1)",
    width: 28,
    height: 28,
  };

  const [hovered, setHovered] = React.useState<number | null>(null);

  return (
    <div
      style={{
        display: "flex",
        gap: "1rem",
        background: "rgba(20,22,24,0.7)",
        padding: "0.25rem 1.5rem",
        borderRadius: "2rem",
        boxShadow: "0 2px 12px rgba(0,0,0,0.18)",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {[onSkipToStart, onPrev, () => (paused ? (onPlay ? onPlay() : null) : onPause ? onPause() : null), onNext, onEnd].map((handler, i) => (
        <button
          key={i}
          onClick={handler}
          title={['Skip to Start', 'Previous', paused ? 'Play' : 'Pause', 'Next', 'End'][i]}
          style={{
            ...buttonStyle,
            ...(hovered === i ? buttonHoverStyle : {}),
          }}
          onMouseEnter={() => setHovered(i)}
          onMouseLeave={() => setHovered(null)}
          tabIndex={0}
        >
          <img
            style={imgStyle}
            src={[
              skiptostart,
              rewind,
              paused ? play : pause,
              ff,
              end,
            ][i]}
            alt={['Skip to Start', 'Previous', paused ? 'Play' : 'Pause', 'Next', 'End'][i]}
          />
        </button>
      ))}
    </div>
  );
};

export default AnimControls;
