import { XMLParser } from 'fast-xml-parser';
import React, { Component } from 'react';
import withRouter from '../functions/withRouter';
import { Link } from "react-router-dom";
import StoryV1 from './StoryV1';
import StoryV2 from './StoryV2';

class Trek extends Component {
  constructor(props) {
    super(props);
    this.state = {
      trekId: this.props.router.params.id,
      versions: {
        v2: "005"
      }
    };
    this.addOption = this.addOption.bind(this);
    this.voteForOption = this.voteForOption.bind(this);
  }

  componentDidMount() {
    fetch(`https://texttrek.azurewebsites.net/api/get?trek=${this.state.trekId}&code=6-41OE76Gc55lz7CzSvZDbEgl4AZ57NtNTKom0L46EmgAzFuT4Qrbw==`)
        .then(res => res.json())
        .then(votes => this.setState({ votes: votes }));
  }

  addOption() {
    fetch(`https://texttrek.azurewebsites.net/api/add?trek=${this.state.trekId}&code=Tc0wVgJLyF2qWwP_28jQDKmXHweUNmqLPWSWeqDYPk-pAzFumYHhHg==`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ "option": this.state.option })
    })
      .then(res => {
        if (res.status == 200) {
          window.location.reload(false)
        } else {
          res.text().then(text => this.setState({ error: text }))
        }
      });
  }

  voteForOption(option) {
    fetch(`https://texttrek.azurewebsites.net/api/vote?trek=${this.state.trekId}&code=fo3t-iTERsxIBAyW48q90lipinQ52NbfPYThshOdmrTPAzFuA4f8PQ==`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ "option": option })
    })
      .then(res => {
        if (res.status == 200) {
          window.location.reload(false)
        } else {
          res.text().then(text => this.setState({ error: text }))
        }
      });
  }

  getTotalVotes() {
    return;
  }

  render() {
    var totalVotes = this.getTotalVotes();
    return (
      <div className="container mx-auto max-w-4xl mb-5">
        <Link to="/">
          <h1 className="text-3xl font-bold center p-5">
            <img className="mix-blend-darken m-auto invert hover:opacity-80" width="150px" src="./texttrek.jpg"></img>
          </h1>
        </Link>
        {this.state.trekId < this.state.versions.v2 ?
          <StoryV1 trekId={this.state.trekId} /> :
          <StoryV2 trekId={this.state.trekId} />
        }

        {Array.isArray(this.state.votes) && this.state.votes.map((v) => (
          <VoteOption
            key={v.option}
            option={v.option}
            votes={v.votes}
            totalVotes={Math.max(...this.state.votes.map(x => x.votes))}
            onVote={this.voteForOption}
          />
        ))}

        {this.state.error ?
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mb-5 relative shadow-lg" role="alert">
          <span className="block sm:inline">{this.state.error}</span>
          <span className="absolute top-0 bottom-0 right-0 px-4 py-3" onClick={() => this.setState({ error: null })}>
            <svg className="fill-current h-6 w-6 text-red-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><title>Close</title><path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z" /></svg>
          </span>
        </div> : <></>}

        <div className="flex shadow-lg">
          <input className="flex-grow p-2 border border-r-0 border-gray-300" type="text" placeholder="Suggest a new option..." onChange={(ev) => this.setState({ option: ev.currentTarget.value })}/>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 focus:outline-none focus:shadow-outline" onClick={this.addOption}>Add</button>
        </div>
      </div>
    );
  }
}

export default withRouter(Create);