import './App.css';
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Trek from './pages/Trek';
import Home from './pages/Home';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<Home />} />
        <Route exact path="/trek/:id" element={<Trek  />} />
      </Routes>
    </Router>
  );
};

export default App;