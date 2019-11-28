import React from 'react';
import axios from 'axios'
import { BrowserRouter as Router, Route, Redirect} from "react-router-dom";

import './App.css'

import HomePage from './components/HomePage'
import InstructionCard from './components/InstructionCard'
import Layout from './components/Layout'


function App() {
  return (
    <Router>
      <Route exact path="/" component={LandingPage}/>
      <Route path="/logged_in" component={HomePage} />
      <Route path="/auth_error" component={AuthError}/>
    </Router>
  );
}


class LandingPage extends React.Component{
  constructor(props) {
    super(props);
    this.state = {
      redirect_url: 0,
      authError: false
    };
  }

  componentDidMount(){
    axios.get(process.env.REACT_APP_API_BASE_URL + '/authorize')
    .then((res) => {
      if (res.status !== 200){
        this.setState({authError: true})
      }
      this.setState({redirect_url: res.data['redirect_url']});
    })
  }
  redirect = () =>{
      window.location.replace(this.state.redirect_url);
  } 
  render(){
    if (this.state.authError)
      return <Redirect to="/auth_error"/>;

    const page_top = (
    <div style={{width: "100%", height: "100%", backgroundColor: "rgba(0, 0, 0, 0.4)", display: "flex", flexDirection: "column", justifyContent: "center"}}>
      <p className="call-to-action">
        {"Save tracks from your favorite YouTube DJ sets as Spotify Playlists"}
      </p>
    </div>
    );
    const page_bottom = (
      <React.Fragment>
        <div className="PageContainer">
          <div className="CardContainer">
            <InstructionCard text="Copy the link of a DJ set on YouTube" bgimg="youtube-logotype.png"/>
            <InstructionCard text="Paste your link in the bar on the next page" bgimg="paste.png"/>          
            <InstructionCard text="The tool searches for a tracklist and creates your playlist" bgimg="chip.png"/>
          </div>
          <button className="log-in-btn" onClick={this.redirect}>Log in with Spotify</button>
        </div>
      </React.Fragment>
    )
    return(
      <Layout top={page_top} bottom={page_bottom}/>
    )
  }
}


const AuthError = () =>(
  <h2>Authorization Failed</h2>
);



export default App;
