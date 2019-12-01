import React from 'react';
import { Redirect } from 'react-router-dom'
import axios from 'axios'
import queryString from 'query-string'

import './HomePage.css';

import Layout from './Layout'
import Drawer from './Drawer'

axios.defaults.timeout = 70000;
const yt_regex = new RegExp("http(?:s?):\\/\\/(?:www\\.)?youtu(?:be\\.com\\/watch\\?v=|\\.be\\/)([\\w\\-\\_]*)(&(amp;)?[\\w\\?‌​=]*)?");


class HomePage extends React.Component {
    constructor(props){
      super(props);
      this.state = {
        authError: false,
        drawerOpen: false, 
        inputText: "",
        tracks: [],
        video_title: "",
        inputError: false,
        loading: false,
        noTracksFound: false
      }
    }

    componentDidMount(){
      axios.get(process.env.REACT_APP_API_BASE_URL + '/token?code=' + 
                queryString.parse(this.props.location.search).code,
                {withCredentials: true})
      .then((res) => {
        if (res.status !== 200)
          this.setState({authError: true});
      }) 
    }

    validateAndSubmit = () => {
      this.setState({
        drawerOpen: false,
        tracks: null,
        inputError: false,
        loading: true,
        noTracksFound: false})
      if (yt_regex.test(this.state.inputText)){
        axios.get(process.env.REACT_APP_API_BASE_URL + '/tracks?link=' + 
                  this.state.inputText, {withCredentials: true})
        .then((res) => {
            this.setState({
              drawerOpen: true,
              tracks: res.data['tracks'],
              video_title: res.data['video_title'],
              loading: false})
        })
        .catch((error)=>{
            this.setState({noTracksFound: true,
            loading: false})
        })
      } else {
        this.setState({inputError: true, loading: false})
      }
    }
    handleInputChange = (e) => {
      this.setState({inputText: e.target.value})
    }
    render(){
      if (this.state.authError)
        return <Redirect to="/auth_error"/>;

      var inputErrorMessage = null;
      if (this.state.inputError)
        inputErrorMessage = <p style={{color: "red"}}>Not a valid YouTube link</p>

      var loadingSpinner = null;
      if (this.state.loading)
        loadingSpinner = (<React.Fragment>
                          <div class="lds-facebook"><div></div><div></div><div></div></div>
                          <p>Looking for your tracklist</p>
                         </React.Fragment>);

      var noTracksFoundError = null;
      if (this.state.noTracksFound)
          noTracksFoundError = <p>Could not find any tracks for your mix.</p>
      const bar = (
        <div className="input-container">
          <div style={{display: "flex", marginTop: "-30px", width: "100%",  verticalAlign:"top", height: "60px" }}>
            <input id="link-input" type="text" placeholder="Paste your YouTube URL here..." onChange={this.handleInputChange}/>
            <button className="submit-btn" onClick={this.validateAndSubmit}>Submit</button>
          </div>
          {inputErrorMessage}
          {noTracksFoundError}
          {loadingSpinner}
          <Drawer open={this.state.drawerOpen} tracks={this.state.tracks} video_title={this.state.video_title}/>
        </div>
      );
      return(
          <Layout bottom={bar}/>
        )
    }

}

export default HomePage;