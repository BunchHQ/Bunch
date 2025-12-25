import type React from "react"

interface ReplySpineProps {
  onClick?: () => void
  className?: string
}

export const ReplySpine: React.FC<ReplySpineProps> = ({ onClick, className }) => {
  return (
    <div
      className={`absolute top-0 left-8 z-0 flex h-8 w-5 cursor-pointer items-center ${
        className || ""
      }`}
      onClick={onClick}
      style={{ pointerEvents: onClick ? "auto" : "none" }}
      data-testid="message-reply-spine"
    >
      {/* SVG for a 90-degree bent line, like Discord */}
      <svg
        width="16"
        height="32"
        viewBox="0 0 16 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        version="1.1"
        transform="matrix(6.123233995736766e-17,1,-1,6.123233995736766e-17,0,0)"
      >
        <path d="M4 0 V20 Q4 30 15 29 H20" stroke="#9b9ca3" fill="none" strokeWidth="1.5"></path>
      </svg>
    </div>
  )
}
