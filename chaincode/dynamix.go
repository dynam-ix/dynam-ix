/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

/*
 * Smart contract of the Dynam-IX project. Based on the fabcar smart contract.
 */

package main

/* Imports
 * 4 utility libraries for formatting, handling bytes, reading and writing JSON, and string manipulation
 * 2 specific Hyperledger Fabric specific libraries for Smart Contracts
 */
import (
	"bytes"
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/hyperledger/fabric/core/chaincode/shim"
	sc "github.com/hyperledger/fabric/protos/peer"
)

// Define the Smart Contract structure
type SmartContract struct {
}

// Define the AS structure, with 5 properties.  Structure tags are used by encoding/json library
type AS struct {
	ASN     string `json:"asn"`
	Address string `json:"address"`
	Service string `json:"service"`
	CustRep int    `json:"custrep"`
	ProvRep int    `json:"provrep"`
}

/*
 * The Init method is called when the Smart Contract "dynamix" is instantiated by the blockchain network
 * Best practice is to have any Ledger initialization in separate function -- see initLedger()
 */
func (s *SmartContract) Init(APIstub shim.ChaincodeStubInterface) sc.Response {
	return shim.Success(nil)
}

/*
 * The Invoke method is called as a result of an application request to run the Smart Contract "dynamix"
 * The calling application program has also specified the particular smart contract function to be called, with arguments
 */
func (s *SmartContract) Invoke(APIstub shim.ChaincodeStubInterface) sc.Response {

	// Retrieve the requested Smart Contract function and arguments
	function, args := APIstub.GetFunctionAndParameters()
	// Route to the appropriate handler function to interact with the ledger appropriately
	if function == "query" {
		return s.query(APIstub, args)
	} else if function == "initLedger" {
		return s.initLedger(APIstub)
	} else if function == "register" {
		return s.register(APIstub, args)
	} else if function == "list" {
		return s.list(APIstub)
	} else if function == "history" {
		return s.history(APIstub, args)
	} else if function == "delete" {
		return s.delete(APIstub, args)
	} else if function == "updateCustRep" {
		return s.updateCustRep(APIstub, args)
	} else if function == "updateProvRep" {
		return s.updateProvRep(APIstub, args)
	} else if function == "updateService" {
		return s.updateService(APIstub, args)
	} else if function == "updateAddress" {
		return s.updateAddress(APIstub, args)
	}

	return shim.Error("Invalid Smart Contract function name.")
}

func (s *SmartContract) query(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	ASAsBytes, _ := APIstub.GetState(args[0])
	return shim.Success(ASAsBytes)
}

func (s *SmartContract) initLedger(APIstub shim.ChaincodeStubInterface) sc.Response {
	ASes := []AS{
		AS{ASN: "1234", Address: "10.1.1.50:5000", Service: "DDoS Mitigation", CustRep: 10, ProvRep: 100},
		AS{ASN: "5678", Address: "10.1.1.60:5000", Service: "Transit Provider", CustRep: -1, ProvRep: 34},
		AS{ASN: "1590", Address: "10.1.1.70:5000", Service: "Cloud Provider", CustRep: 5, ProvRep: 12},
	}

	i := 0
	for i < len(ASes) {
		fmt.Println("i is ", i)
		ASAsBytes, _ := json.Marshal(ASes[i])
		APIstub.PutState("AS"+strconv.Itoa(i), ASAsBytes)
		fmt.Println("Added", ASes[i])
		i = i + 1
	}

	return shim.Success(nil)
}

func (s *SmartContract) register(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 6 {
		return shim.Error("Incorrect number of arguments. Expecting 6")
	}

	custRep, err := strconv.Atoi(args[4])
	if err != nil {
		return shim.Error(err.Error())
	}

	provRep, err := strconv.Atoi(args[5])
	if err != nil {
		return shim.Error(err.Error())
	}

	var as = AS{ASN: args[1], Address: args[2], Service: args[3], CustRep: custRep, ProvRep: provRep}

	ASAsBytes, _ := json.Marshal(as)
	APIstub.PutState(args[0], ASAsBytes)

	return shim.Success(nil)
}

func (s *SmartContract) list(APIstub shim.ChaincodeStubInterface) sc.Response {

	startKey := "AS0"
	endKey := "AS999"

	resultsIterator, err := APIstub.GetStateByRange(startKey, endKey)
	if err != nil {
		return shim.Error(err.Error())
	}
	defer resultsIterator.Close()

	// buffer is a JSON array containing QueryResults
	var buffer bytes.Buffer
	buffer.WriteString("[")

	bArrayMemberAlreadyWritten := false
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return shim.Error(err.Error())
		}
		// Add a comma before array members, suppress it for the first array member
		if bArrayMemberAlreadyWritten == true {
			buffer.WriteString(",")
		}
		buffer.WriteString("{\"Key\":")
		buffer.WriteString("\"")
		buffer.WriteString(queryResponse.Key)
		buffer.WriteString("\"")

		buffer.WriteString(", \"Record\":")
		// Record is a JSON object, so we write as-is
		buffer.WriteString(string(queryResponse.Value))
		buffer.WriteString("}")
		bArrayMemberAlreadyWritten = true
	}
	buffer.WriteString("]")

	fmt.Printf("- queryAllASes:\n%s\n", buffer.String())

	return shim.Success(buffer.Bytes())
}

func (s *SmartContract) updateCustRep(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 2 {
		return shim.Error("Incorrect number of arguments. Expecting 2")
	}

	ASAsBytes, _ := APIstub.GetState(args[0])
	as := AS{}

	json.Unmarshal(ASAsBytes, &as)
	rep, err := strconv.Atoi(args[1])
	if err != nil {
		return shim.Error(err.Error())
	}

	as.CustRep = as.CustRep + rep

	ASAsBytes, _ = json.Marshal(as)
	APIstub.PutState(args[0], ASAsBytes)

	return shim.Success(nil)
}

func (s *SmartContract) updateProvRep(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 2 {
		return shim.Error("Incorrect number of arguments. Expecting 2")
	}

	ASAsBytes, _ := APIstub.GetState(args[0])
	as := AS{}

	json.Unmarshal(ASAsBytes, &as)
	rep, err := strconv.Atoi(args[1])
	if err != nil {
		return shim.Error(err.Error())
	}

	as.ProvRep = as.ProvRep + rep

	ASAsBytes, _ = json.Marshal(as)
	APIstub.PutState(args[0], ASAsBytes)

	return shim.Success(nil)
}

func (s *SmartContract) updateService(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 2 {
		return shim.Error("Incorrect number of arguments. Expecting 2")
	}

	ASAsBytes, _ := APIstub.GetState(args[0])
	as := AS{}

	json.Unmarshal(ASAsBytes, &as)
	as.Service = args[1]

	ASAsBytes, _ = json.Marshal(as)
	APIstub.PutState(args[0], ASAsBytes)

	return shim.Success(nil)
}

func (s *SmartContract) updateAddress(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 2 {
		return shim.Error("Incorrect number of arguments. Expecting 2")
	}

	ASAsBytes, _ := APIstub.GetState(args[0])
	as := AS{}

	json.Unmarshal(ASAsBytes, &as)
	as.Address = args[1]

	ASAsBytes, _ = json.Marshal(as)
	APIstub.PutState(args[0], ASAsBytes)

	return shim.Success(nil)
}

// Deletes an entity from state
func (s *SmartContract) delete(stub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	A := args[0]

	// Delete the key from the state in ledger
	err := stub.DelState(A)
	if err != nil {
		return shim.Error("Failed to delete state")
	}

	return shim.Success(nil)
}

func (s *SmartContract) history(stub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) < 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	asn := args[0]

	fmt.Printf("- history for asn: %s\n", asn)

	resultsIterator, err := stub.GetHistoryForKey(asn)
	if err != nil {
		return shim.Error(err.Error())
	}
	defer resultsIterator.Close()

	// buffer is a JSON array containing historic values for the AS
	var buffer bytes.Buffer
	buffer.WriteString("[")

	bArrayMemberAlreadyWritten := false
	for resultsIterator.HasNext() {
		response, err := resultsIterator.Next()
		if err != nil {
			return shim.Error(err.Error())
		}
		// Add a comma before array members, suppress it for the first array member
		if bArrayMemberAlreadyWritten == true {
			buffer.WriteString(",")
		}
		buffer.WriteString("{\"TxId\":")
		buffer.WriteString("\"")
		buffer.WriteString(response.TxId)
		buffer.WriteString("\"")

		buffer.WriteString(", \"Value\":")
		// if it was a delete operation on given key, then we need to set the
		//corresponding value null. Else, we will write the response.Value
		//as-is (as the Value itself a JSON AS)
		if response.IsDelete {
			buffer.WriteString("null")
		} else {
			buffer.WriteString(string(response.Value))
		}

		buffer.WriteString(", \"Timestamp\":")
		buffer.WriteString("\"")
		buffer.WriteString(time.Unix(response.Timestamp.Seconds, int64(response.Timestamp.Nanos)).String())
		buffer.WriteString("\"")

		buffer.WriteString(", \"IsDelete\":")
		buffer.WriteString("\"")
		buffer.WriteString(strconv.FormatBool(response.IsDelete))
		buffer.WriteString("\"")

		buffer.WriteString("}")
		bArrayMemberAlreadyWritten = true
	}
	buffer.WriteString("]")

	fmt.Printf("\n%s\n", buffer.String())

	return shim.Success(buffer.Bytes())
}

// The main function is only relevant in unit test mode. Only included here for completeness.
func main() {

	// Create a new Smart Contract
	err := shim.Start(new(SmartContract))
	if err != nil {
		fmt.Printf("Error creating new Smart Contract: %s", err)
	}
}
