/*=========================================================================
 *
 *  Copyright Leiden University Medical Center, Erasmus University Medical 
 *  Center and contributors
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0.txt
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 *=========================================================================*/

#include "selxItkGradientDescentOptimizerv4.h"

namespace selx
{
  template<class InternalComputationValueType>
  ItkGradientDescentOptimizerv4Component< InternalComputationValueType>::ItkGradientDescentOptimizerv4Component()
{
  m_Optimizer = GradientDescentOptimizerv4Type::New();
  m_Optimizer->SetNumberOfIterations(100);
  m_Optimizer->SetLearningRate(1.0);
  
  //TODO: instantiating the filter in the constructor might be heavy for the use in component selector factory, since all components of the database are created during the selection process.
  // we could choose to keep the component light weighted (for checking criteria such as names and connections) until the settings are passed to the filter, but this requires an additional initialization step.
}

template<class InternalComputationValueType>
ItkGradientDescentOptimizerv4Component< InternalComputationValueType>::~ItkGradientDescentOptimizerv4Component()
{
}

template<class InternalComputationValueType>
typename ItkGradientDescentOptimizerv4Component< InternalComputationValueType>::Optimizerv4Pointer ItkGradientDescentOptimizerv4Component< InternalComputationValueType>::GetItkOptimizerv4()
{
  
  return (Optimizerv4Pointer) this->m_Optimizer;
}
template<class InternalComputationValueType>
bool
ItkGradientDescentOptimizerv4Component< InternalComputationValueType>
::MeetsCriterion(const ComponentBase::CriterionType &criterion)
{
  bool hasUndefinedCriteria(false);
  bool meetsCriteria(false);
  if (criterion.first == "ComponentProperty")
  {
    meetsCriteria = true;
    for (auto const & criterionValue : criterion.second) // auto&& preferred?
    {
      if (criterionValue != "SomeProperty")  // e.g. "GradientDescent", "SupportsSparseSamples
      {
        meetsCriteria = false;
      }
    }
  }
  return meetsCriteria;
}

} //end namespace selx
