import React from 'react'
import "./Header.css"

const Header = () => (
  <div className="Header">
      <p>Sets to Spotify </p><img src="dj.svg" alt="dj-icon.svg"/>
      <div className="HeaderTabs">
      <a href="mailto:setstospotify@gmail.com" target="_blank">Get Support</a>
      <a href="https://github.com/akjadoon/sets-to-spotify" target="_blank">View on Gitub</a>
      </div>
  </div>
);

export default Header;
