import './App.css';
import React from 'react';
import { HashRouter, Route, Routes } from "react-router-dom";
import Trek from './pages/Trek';
import Home from './pages/Home';

const App = () => {
  return (
    <HashRouter>
      <Routes>
        <Route exact path="/" element={<Home />} />
        <Route exact path="/trek/:id" element={<Trek  />} />
      </Routes>
    </HashRouter>
  );
};

export default App;