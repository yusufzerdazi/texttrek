import { XMLParser } from 'fast-xml-parser';
import React, { Component } from 'react';
import withRouter from '../functions/withRouter';

class StoryV2 extends Component {
    constructor(props) {
        super(props);
        console.log(props)
        this.state = {
            trek: null,
            trekId: this.props.trekId,
            downloadedBlobs: {}
        };
    }

    componentDidMount() {
        fetch(`https://texttrek.blob.core.windows.net/treks?restype=container&comp=list&prefix=${this.state.trekId}`)
            .then(res => res.text())
            .then(text => new XMLParser().parse(text).EnumerationResults.Blobs.Blob)
            .then(blobs => {
                if (!blobs) {
                    return;
                }
                var text = (Array.isArray(blobs) ? blobs : [blobs]).filter(blob => blob.Name.endsWith(".txt"));
                var images = (Array.isArray(blobs) ? blobs : [blobs]).filter(blob => blob.Name.endsWith(".png") || blob.Name.endsWith(".jpeg"));
                var combined = text
                    .map(b => {return {"text": b, "image": images.filter(x => x.Name.split(".")[0] == b.Name.split(".")[0])[0]}});
                console.log(combined)
                this.setState({ trek: combined });
                blobs.map(blob => fetch(blob.Url)
                    .then(res => res.text())
                    .then(text => {
                        this.setState({ [blob.Name]: JSON.parse(text) });
                        if(blob.Name.endsWith("000.txt")) {
                            this.setState({ initial: JSON.parse(text) });
                        }
                    }))
            });
    }

    render() {
        return (
            <div className="space-y-5 w-full mb-5">
                {this.state.trek && this.state.initial ? <>
                    <h3>{this.state.initial.title}</h3>
                    <div className="grid grid-cols-6 2xs: 2xl:fixed 2xl:top-5 2xl:left-5 2xl:w-72 bg-white shadow-md z-10">
                        <div className="p-5 col-span-2 2xl:col-span-6 "><img className='shadow-xl' src={this.state.trek[0]["text"].Url.replace("000.txt", "avatar.jpeg")}></img></div>
                        <div className="py-5 2xl:p-5 2xl:pt-0 pr-5 col-span-4 2xl:col-span-6 ">
                            <p className="text-gray-700 text-lg leading-relaxed"><b>Name: </b>{this.state.initial.character.name}.</p>
                            <p className="text-gray-700 text-lg leading-relaxed"><b>Age: </b>{this.state.initial.character.age}.</p>
                            <p className="text-gray-700 text-lg leading-relaxed"><b>Race: </b>{this.state.initial.character.race}.</p>
                            <p className="text-gray-700 text-lg leading-relaxed"><b>Gender: </b>{this.state.initial.character.gender}.</p>
                            <p className="text-gray-700 text-lg leading-relaxed"><b>Alignment: </b>{this.state.initial.character.alignment}.</p>
                            <p className="text-gray-700 text-lg leading-relaxed"><b>Backstory: </b>{this.state.initial.character.backstory}</p>
                        </div>
                    </div>
                    <div className="grid grid-cols-6  2xl:fixed 2xl:top-0 2xl:right-5 2xl:w-72 bg-white shadow-md z-10">
                        <div className="p-5 col-span-2 2xl:col-span-6"><img className='shadow-xl' src={this.state.trek[0]["text"].Url.replace("000.txt", "setting.jpeg")}></img></div>
                        <div className="py-5 2xl:p-5 2xl:pt-0 pr-5 col-span-4 2xl:col-span-6">
                            <p className="text-gray-700 text-lg leading-relaxed"><b>Planet: </b>{this.state.initial.setting.planet}.</p>
                            <p className="text-gray-700 text-lg leading-relaxed"><b>Year: </b>{this.state.initial.setting.year}.</p>
                            <p className="text-gray-700 text-lg leading-relaxed"><b>Location: </b>{this.state.initial.setting.location}.</p>
                            <p className="text-gray-700 text-lg leading-relaxed"><b>Description: </b>{this.state.initial.setting.description}.</p>
                        </div>
                    </div>
                    {this.state.trek.map((trek, index) => (
                    this.state[trek["text"].Name] ? <div className={`flex flex-col space-y-3 p-5 bg-white shadow-lg`} key={"" + index}>
                        <img className="m-auto" src={trek["image"].Url} alt="" />
                        <div>
                        {this.state[trek["text"].Name].prompt.split('\n').map((p, i) => (
                            <p className="text-gray-700 text-lg leading-relaxed" key={"" + i}>{p}</p>
                        ))}
                        </div>
                    </div> : <></>
                ))}</> : <></>}
            </div>
        );
    }
}

export default withRouter(StoryV2);