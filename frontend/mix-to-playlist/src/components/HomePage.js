import React from 'react';
import { Redirect } from 'react-router-dom'
import axios from 'axios'
import Cookies from 'universal-cookie'
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
        video_title: ""
      }
    }

    componentDidMount(){
      axios.get(process.env.REACT_APP_API_BASE_URL + '/token?code=' + 
                queryString.parse(this.props.location.search).code,
                {withCredentials: true})
      .then((res) => {
        if (res.status != 200)
          this.setState({authError: true});
      }) 
    }

    validateAndSubmit = () => {
      if (yt_regex.test(this.state.inputText)){
        this.setState({
          drawerOpen: false,
          tracks: null})

        axios.get(process.env.REACT_APP_API_BASE_URL + '/tracks?link=' + 
                  this.state.inputText, {withCredentials: true})
        .then((res) => {
          this.setState({
            drawerOpen: true,
            tracks: res.data['tracks'],
            video_title: res.data['video_title']})
        })
      } else {
        //Not a valid YT lnk
      }
    }
    handleInputChange = (e) => {
      this.setState({inputText: e.target.value})
    }
    render(){
      if (this.state.authError)
        return <Redirect to="/auth_error"/>;

      const bar = (
        <div className="input-container">
          <div style={{display: "flex", alignItems: "center", marginTop: "-25px", width: "100%",  verticalAlign:"top" }}>
            <label for="link-input">Enter a link</label>
            <input id="link-input" type="text" placeholder="Paste your YouTube URL here..." onChange={this.handleInputChange}/>
            <button className="submit-btn" onClick={this.validateAndSubmit}>Submit</button>
          </div>
          <Drawer open={this.state.drawerOpen} tracks={this.state.tracks} video_title={this.state.video_title}/>
        </div>
      );
      return(
          <Layout bottom={bar}/>
        )
    }

}

export default HomePage;