import './App.css';
import { XMLParser } from 'fast-xml-parser';
import React, { Component } from 'react';

class App extends Component {
  constructor(props){
    super(props);
    this.state = {
      trek: null,
      downloadedBlobs: {}
    };
  }

  componentDidMount(){
    console.log("test")
    fetch("https://texttrek.blob.core.windows.net/treks?restype=container&comp=list&prefix=000")
      .then(res => res.text())
      .then(text => new XMLParser().parse(text).EnumerationResults.Blobs.Blob)
      .then(blobs => {
        this.setState({trek: blobs});
        blobs.filter(blob => !blob.Name.endsWith("summary.txt") && blob.Name.endsWith(".txt")).map(blob => fetch(blob.Url)
          .then(res => res.text())
          .then(text => this.setState({[blob.Name]: text})))
      });
  }

  render() {
    return <div className="container mx-auto items-center max-w-4xl" >
      <h1 className="text-3xl font-bold text-center p-5 pb-0">
        Text Trek <i className='far fa-swords'></i>
      </h1>
      { this.state.trek ? this.state.trek.map(trek => {
        if(trek.Name.endsWith(".png")){
          return <div className="p-5">
            <img key={trek.Name} width="100%" className='m-auto shadow-xl rounded-2xl max-w-md' src={trek.Url}></img>
          </div>
        } else {
          return this.state[trek.Name] ? <div className='shadow-xl bg-white p-5 rounded-2xl' key={trek.Name}>{this.state[trek.Name].split("\n").map(
            (p, i) => <p key={i} className='italic indent-4 '>{p}</p>
          )}</div> : <></>
        }
      }) : <></> }
    </div>
  }
}

export default App;