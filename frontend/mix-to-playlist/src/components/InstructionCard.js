import React from 'react';
import './InstructionCard.css';


const InstructionCard = (props) => {
    return(
            <div className="Card">
                <img src={props.bgimg} alt={props.bgimg}/>
                <div style={{padding: "0px 20px", fontSize: "25px"}}>
                    <p><strong>{props.text}</strong></p>
                </div>
            </div>
    )
}

export default InstructionCard;