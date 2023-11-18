import './App.css';
import React from 'react';
import { HashRouter, Route, Routes } from "react-router-dom";
import Trek from './pages/Trek';
import Home from './pages/Home';
import Create from './pages/Create';

const App = () => {
  return (
    <HashRouter>
      <Routes>
        <Route exact path="/" element={<Home />} />
        <Route exact path="/trek/:id" element={<Trek  />} />
        <Route exact path="/create" element={<Create  />} />
      </Routes>
    </HashRouter>
  );
};

export default App;