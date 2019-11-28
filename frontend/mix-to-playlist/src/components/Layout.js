import React from 'react'
import Header from './Header'


const pageStyle = {
    height: "100%",
    backgroundColor: "whitesmoke",
    minHeight: "100vh",
    margin: "0", 
    display: "flex",
    flexDirection: "column"
}

const pageTopStyle = {
    height: "40vh",
    width:"100%",
    backgroundImage: "url(gray-turntable.jpg)",
    backgroundSize: "cover",
    backgroundPosition: "center"
}

const Layout = (props) => (
    <div style={pageStyle}>
    <Header/>
    <div style={{textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center"}}>
      <div style={pageTopStyle}>
        {props.top}
      </div>
        {props.bottom}
    </div>
  </div>
);

export default Layout;