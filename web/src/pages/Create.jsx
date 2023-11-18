import { XMLParser } from 'fast-xml-parser';
import React, { Component } from 'react';
import withRouter from '../functions/withRouter';
import { Link } from "react-router-dom";
import StoryV1 from './StoryV1';
import StoryV2 from './StoryV2';

class Create extends Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.createStory = this.createStory.bind(this);
  }

  componentDidMount() {

  }

  createStory() {
    fetch(`https://texttrek.azurewebsites.net/api/create?code=z_lDtm4wMjhdJmkFX9robm3944SgBImGlSGOvzA_VyRDAzFuPvMsCA==`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ "prompt": this.state.prompt })
    })
      .then(res => {
        if (res.status == 200) {
          window.location.reload(false)
        } else {
          res.text().then(text => this.setState({ error: text }))
        }
      });
  }

  render() {
    return (
      <div className="container mx-auto max-w-4xl mb-5">
        <Link to="/">
          <h1 className="text-3xl font-bold center p-5">
            <img className="mix-blend-darken m-auto invert hover:opacity-80" width="150px" src="./texttrek.jpg"></img>
          </h1>
        </Link>

        {this.state.error ?
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mb-5 relative shadow-lg" role="alert">
          <span className="block sm:inline">{this.state.error}</span>
          <span className="absolute top-0 bottom-0 right-0 px-4 py-3" onClick={() => this.setState({ error: null })}>
            <svg className="fill-current h-6 w-6 text-red-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><title>Close</title><path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z" /></svg>
          </span>
        </div> : <></>}

        <div className="flex shadow-lg">
          <textarea className="create flex-grow p-2 border border-r-0 border-gray-300" type="text" placeholder="Write a prompt for a new story. The prompt can include information for the character, setting, backstory and anything else you find relevant." onChange={(ev) => this.setState({ prompt: ev.currentTarget.value })}/>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 focus:outline-none focus:shadow-outline" onClick={this.createStory}>Create</button>
        </div>
      </div>
    );
  }
}

export default withRouter(Create);