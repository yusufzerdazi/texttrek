import './App.css';
import { Parser } from 'xml2js';
import React, { Component } from 'react';

class App extends Component {
  constructor(props){
    console.log("test")
    super(props);
  }

  componentDidMount(){
    console.log("test")
    var blobs = fetch("https://texttrek.blob.core.windows.net/treks?restype=container&comp=list&prefix=000")
      .then(res => res.text())
      .then(text => this.setState({trek: Parser.parseString(text)}));
  }

  render() {
    return <h1 className="text-3xl font-bold underline">
      Hello world!
    </h1>
  }
}

export default App;