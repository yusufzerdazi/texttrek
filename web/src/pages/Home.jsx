import { XMLParser } from 'fast-xml-parser';
import React, { Component } from 'react';
import { Link } from "react-router-dom";

class Home extends Component {
    constructor(props){
      super(props);
      this.state = {
        trek: null,
        downloadedBlobs: {}
      };
    }
  
    componentDidMount(){
      console.log("test")
      fetch("https://texttrek.blob.core.windows.net/treks?restype=container&comp=list")
        .then(res => res.text())
        .then(text => new XMLParser().parse(text).EnumerationResults.Blobs.Blob)
        .then(blobs => {
          var treks = [...new Set(blobs.map(b => b.Name.split("/")[0]))]
          console.log(treks);
          this.setState({treks: blobs.filter(b => treks.some(t => b.Name.startsWith(t)) && b.Name.endsWith("000.png"))});
          // blobs.filter(blob => !blob.Name.endsWith("summary.txt") && blob.Name.endsWith(".txt")).map(blob => fetch(blob.Url)
          //   .then(res => res.text())
          //   .then(text => this.setState({[blob.Name]: text})))
        });
    }
  
    render() {
      return <div className="container mx-auto items-center max-w-4xl pb-5" >
        <h1 className="text-3xl font-bold text-center p-5">
          Text Trek <i className='far fa-swords'></i>
        </h1>
        <p className='italic text-center'>Text Trek is a community-based, AI driven text based adventure game. Imagine huge persistent worlds spanning centuries, characters finding artifacts from past generations, and thrilling open-ended plotlines with atmospheric artwork. It's not there yet, but it's still pretty cool.</p>
        <div className='mt-5 mb-5 grid grid-cols-3 gap-4'>
        { this.state.treks ? this.state.treks.map(t => <div><Link to={"trek/" + t.Name.split("/")[0]}><img key={t.Name} className='shadow-xl rounded-2xl hover:opacity-80' src={t.Url}></img></Link></div>) : <></> }
        </div>
      </div>
    }
}
  
export default Home;