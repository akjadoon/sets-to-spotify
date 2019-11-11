import React from 'react'
import axios from 'axios'

import './Drawer.css'


class Drawer extends React.Component {
    constructor(props){
        super(props);
        this.state = {drawerStyle: {height: "0px"}, content: "tracks"}
    }

    handleSavePlaylist = () => {
        axios.post(process.env.REACT_APP_API_BASE_URL + '/playlist',
                  {
                      track_ids: this.props.tracks.map((t)=>( t.id)),
                      video_title: this.props.video_title
                  },
                  {headers: {"Content-Type": "application/json"},
                   withCredentials: true}
         ).then((res)=>{
            console.log(res.data);
         })
        this.setState({content: "save-playlist"})
    }

    handleDontSavePlaylist = () => {
        this.setState({content: "dont-save-playlist"})
    }

    componentDidUpdate(prevProps){
        if (!prevProps.open && this.props.open)
            this.setState({drawerStyle: {height: "auto"}, content: "tracks"});
        else if (prevProps.open && !this.props.open)
            this.setState({drawerStyle: {height: "0px"}});

    }

    render(){
        var drawerContent = (<p>We're sorry, we couldn't find any tracks for that video. 
            Our tool is constantly being improved. In the mean time, try another link</p>)
        if (this.props.tracks){
            switch(this.state.content){
                case "tracks":
                    var tracks = this.props.tracks.map((t)=>
                        <Track name={t.name} artists={t.artists}/>
                    );
                    drawerContent = (
                        <React.Fragment>
                        <h3 style={{color: "white", textAlign: "left", padding: "5px 20px"}}>Found these songs</h3>
                        <div  className="Drawer-content">
                        {tracks}
                        </div>
                        <div style={{marginBottom: "20px", paddingLeft: "20px"}}>
                            <p>Would you like to save them?</p>
                            <button className="save-playlist-btn btn-yes" onClick={this.handleSavePlaylist}>Yes</button>
                            <button className="save-playlist-btn btn-no" onClick={this.handleDontSavePlaylist}>No</button>
                        </div>
                        </React.Fragment>
                    );
                    break;
                case "save-playlist":
                    drawerContent = (
                        <p className="msg">The playlist has been added to your Spotify account.
                             Please be patient as it can take a few minutes to appear.</p>
                    )
                    break;
                case "dont-save-playlist":
                    drawerContent = (<p className="msg">The playlist was not created.</p>)
                    break;
            }

        }
        return (
            <div style={this.state.drawerStyle} className="Drawer">
                {drawerContent}
            </div>

        )
    }

}

const Track = (props) => (
    <div style={{textAlign: "left", padding: "5px 20px", display: "flex", flexDirection: "column"}}>
      <p style={{color: "white", fontSize: "17px", lineHeight: "5px"}}>{props.name}</p>
      <div style={{display: "flex"}}>
      {props.artists.map((a)=> (
          <p style={{color: "grey", fontSize: "14px",  lineHeight: "5px"}}>{a}</p>
      ))}
      </div>

      
    </div>
  );

export default Drawer;