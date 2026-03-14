import { useState } from 'react';

export default function App() {
  const [isClicked, setIsClicked] = useState(false);

  const handleClick = () => {
    setIsClicked(!isClicked);
  };

  return (
    <div onClick={handleClick}>
      {isClicked ? 'Clicked!' : 'Hi'}
    </div>
  );
}