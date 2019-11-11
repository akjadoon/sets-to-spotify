import React from 'react';
import './InstructionCard.css';


const InstructionCard = (props) => {
    return(
            <div className="Card">
                <img src={props.bgimg} alt={props.bgimg} style={{borderBottom: "8px solid black"}} width={props.width ? props.width : "100%"}/>
                <div style={{padding: "5px 3px"}}>
                    <p><strong>{props.text}</strong></p>
                </div>
            </div>
    )
}

export default InstructionCard;